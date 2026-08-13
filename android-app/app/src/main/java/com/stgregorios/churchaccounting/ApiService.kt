package com.stgregorios.churchaccounting

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.POST

// Data Classes
data class ApiResponse(
    val success: Boolean,
    val message: String?,
    val data: List<Member>? // Simplified for this example, should use generics ideally
)

data class Member(
    val id: Int,
    val reg_no: String,
    val name: String,
    val phone: String
)

interface ApiService {
    @FormUrlEncoded
    @POST("api.php")
    suspend fun getMembers(
        @Field("action") action: String = "get_members"
    ): ApiResponse

    @FormUrlEncoded
    @POST("api.php")
    suspend fun addMember(
        @Field("action") action: String = "add_member",
        @Field("reg_no") regNo: String,
        @Field("name") name: String,
        @Field("address") address: String,
        @Field("phone") phone: String,
        @Field("email") email: String,
        @Field("status") status: String
    ): ApiResponse

    companion object {
        private const val BASE_URL = "https://orthodoxchurchmysore.in/api/"

        fun create(): ApiService {
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            return retrofit.create(ApiService::class.java)
        }
    }
}
